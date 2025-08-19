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

        return userRepository.save(user)
                .flatMap(savedUser -> {
                    log.info("Saved user: {}", savedUser);
                    return createUserProfile(savedUser)
                            .thenReturn(savedUser);
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
                    updatedUser.setId(id);
                    return userRepository.save(updatedUser);
                });
    }

    public Mono<User> patchUser(String id, Map<String, Object> updates) {
        return userRepository.findById(id).flatMap(user -> {
            updates.forEach((key, value) -> {
                switch (key) {
                    case "username" -> user.setUsername((String) value);
                    case "email" -> user.setEmail((String) value);
                    case "password" -> user.setPassword((String) value);
                    case "cellphoneNumber" -> user.setCellphoneNumber((String) value);
                }
            });
            return userRepository.save(user);
        });
    }
}