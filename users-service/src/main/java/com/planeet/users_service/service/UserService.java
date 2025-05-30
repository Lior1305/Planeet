package com.planeet.users_service.service;
import com.planeet.users_service.model.User;
import com.planeet.users_service.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.Map;

@Service
public class UserService {

    @Autowired
    private  UserRepository userRepository;


    public Flux<User> getAllUsers() {
        return userRepository.findAll();
    }

   /* public Mono<User> getUserById(String id) {
        return userRepository.findById(id);
    }*/
    @GetMapping("/{id}")
    public Mono<ResponseEntity<User>> getUserById(@PathVariable String id) {
        return userRepository.findById(id)
                .map(ResponseEntity::ok)
                .switchIfEmpty(Mono.just(ResponseEntity.notFound().build()));
    }


 public Mono<User> createUser(User user) {
        return userRepository.save(user);
  }

    /*public Mono<User> createUser(User user) {
        return userRepository.save(user)
                .flatMap(savedUser -> {
                    // Send HTTP POST to outing-profile-service
                    return webClient.post()
                            .uri("http://localhost:8081/profiles")  // adjust port if needed
                            .bodyValue(Map.of("userId", savedUser.getId()))
                            .retrieve()
                            .bodyToMono(Void.class)  // assuming no body returned
                            .thenReturn(savedUser);
                });
    }*/


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
                    // Add more fields if necessary
                }
            });
            return userRepository.save(user);
        });
    }

}
