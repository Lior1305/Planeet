package com.planeet.users_service.service;

import com.planeet.users_service.model.User;
import com.planeet.users_service.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.Map;

@Service
public class UserService {

    private final Logger log = LoggerFactory.getLogger(UserService.class);
    private final WebClient webClient;
    private final UserRepository userRepository;

    @Autowired
    public UserService(WebClient webClient, UserRepository userRepository) {
        this.webClient = webClient;
        this.userRepository = userRepository;
    }

    public Flux<User> getAllUsers() {
        return userRepository.findAll();
    }

    public Mono<User> createUser(User user) {
        log.info("Received request to create user: {}", user);

        // Check if email already exists first, then create user
        return userRepository.findByEmail(user.getEmail())
                .hasElement()
                .flatMap(emailExists -> {
                    if (emailExists) {
                        log.error("User with email {} already exists", user.getEmail());
                        return Mono.error(new RuntimeException("User with email " + user.getEmail() + " already exists"));
                    } else {
                        // Email doesn't exist, proceed with user creation
                        return userRepository.save(user)
                                .flatMap(savedUser -> {
                                    log.info("Saved user: {}", savedUser);
                                    return createUserProfile(savedUser)
                                            .thenReturn(savedUser);
                                });
                    }
                });
    }

    private Mono<Void> createUserProfile(User savedUser) {
        Map<String, Object> profileRequest = Map.of(
                "user_id", savedUser.getId(),
                "name", savedUser.getUsername()
        );

        return webClient.post()
                .uri("/profiles")
                .bodyValue(profileRequest)
                .retrieve()
                .toBodilessEntity()
                .doOnError(throwable -> {
                    if (throwable instanceof WebClientResponseException) {
                        WebClientResponseException ex = (WebClientResponseException) throwable;
                        log.error("Profile creation failed with status: {} and body: {}",
                                ex.getStatusCode(), ex.getResponseBodyAsString());
                    } else {
                        log.error("Profile creation failed: {}", throwable.getMessage());
                    }
                })
                .onErrorMap(throwable -> new RuntimeException("Profile creation error: " + throwable.getMessage()))
                .then();
    }

    public Mono<User> getUserById(String id) {
        return userRepository.findById(id);
    }

    public Mono<Void> deleteUser(String id) {
        return userRepository.deleteById(id);
    }

    public Mono<User> updateUser(String id, User updatedUser) {
        return userRepository.findById(id)
                .flatMap(existingUser -> {
                    // Check if email is being changed and if it already exists
                    if (!existingUser.getEmail().equals(updatedUser.getEmail())) {
                        return userRepository.findByEmail(updatedUser.getEmail())
                                .hasElement()
                                .flatMap(emailExists -> {
                                    if (emailExists) {
                                        log.error("Cannot update user: email {} already exists", updatedUser.getEmail());
                                        return Mono.error(new RuntimeException("User with email " + updatedUser.getEmail() + " already exists"));
                                    } else {
                                        return proceedWithUpdate(id, updatedUser);
                                    }
                                });
                    }
                    return proceedWithUpdate(id, updatedUser);
                });
    }
    
    private Mono<User> proceedWithUpdate(String id, User updatedUser) {
        updatedUser.setId(id);
        return userRepository.save(updatedUser);
    }

    public Mono<User> patchUser(String id, Map<String, Object> updates) {
        return userRepository.findById(id).flatMap(user -> {
            // Check if email is being updated and if it already exists
            if (updates.containsKey("email")) {
                String newEmail = (String) updates.get("email");
                if (!user.getEmail().equals(newEmail)) {
                    return userRepository.findByEmail(newEmail)
                            .hasElement()
                            .flatMap(emailExists -> {
                                if (emailExists) {
                                    log.error("Cannot patch user: email {} already exists", newEmail);
                                    return Mono.error(new RuntimeException("User with email " + newEmail + " already exists"));
                                } else {
                                    return proceedWithPatch(user, updates);
                                }
                            });
                }
            }
            return proceedWithPatch(user, updates);
        });
    }
    
    private Mono<User> proceedWithPatch(User user, Map<String, Object> updates) {
        updates.forEach((key, value) -> {
            switch (key) {
                case "username" -> user.setUsername((String) value);
                case "email" -> user.setEmail((String) value);
                case "password" -> user.setPassword((String) value);
                case "cellphoneNumber" -> user.setCellphoneNumber((String) value);
            }
        });
        return userRepository.save(user);
    }
    
    public Mono<Boolean> isEmailAvailable(String email) {
        return userRepository.findByEmail(email)
                .map(user -> false) // Email exists, not available
                .defaultIfEmpty(true); // Email doesn't exist, available
    }
}