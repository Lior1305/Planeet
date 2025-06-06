package com.planeet.users_service.service;
import com.planeet.users_service.controller.UserController;
import com.planeet.users_service.model.User;
import com.planeet.users_service.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.fasterxml.jackson.databind.ObjectMapper;

import jakarta.annotation.PostConstruct;


import java.util.HashMap;
import java.util.Map;

@Service
public class UserService {
    private static final Logger log = LoggerFactory.getLogger(UserController.class);
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Autowired
    private  UserRepository userRepository;

    private WebClient webClient;


    public Flux<User> getAllUsers() {
        return userRepository.findAll();
    }

    @GetMapping("/{id}")
    public Mono<ResponseEntity<User>> getUserById(@PathVariable String id) {
        return userRepository.findById(id)
                .map(ResponseEntity::ok)
                .switchIfEmpty(Mono.just(ResponseEntity.notFound().build()));
    }

    public Mono<User> createUser(User user) {
        log.info("Received a request to create user");
        return userRepository.save(user);

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
                }
            });
            return userRepository.save(user);
        });
    }

}
