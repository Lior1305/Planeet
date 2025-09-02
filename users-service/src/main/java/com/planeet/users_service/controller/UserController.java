package com.planeet.users_service.controller;

import com.planeet.users_service.model.User;
import com.planeet.users_service.service.UserService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.Map;

@RestController
@RequestMapping("/users")   
@CrossOrigin(origins = "*")     // also loosen CORS for testing
public class UserController {

    private final Logger log = LoggerFactory.getLogger(UserController.class);  // Removed 'static'

    private final UserService userService;

    @Autowired
    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping
    public Flux<User> getAllUsers() {
        log.info("Got a request to bring all users");
        return userService.getAllUsers();
    }

    @GetMapping("/{id}")
    public Mono<ResponseEntity<User>> getUserById(@PathVariable String id) {
        return userService.getUserById(id)
                .map(ResponseEntity::ok)
                .defaultIfEmpty(ResponseEntity.notFound().build());
    }

    @PostMapping
    public Mono<ResponseEntity<User>> createUser(@RequestBody User user) {
        return userService.createUser(user)
                .map(ResponseEntity::ok)
                .onErrorResume(e -> {
                    log.error("Error creating user: {}", e.getMessage(), e);
                    
                    // Check if it's an email uniqueness error
                    if (e.getMessage() != null && e.getMessage().contains("already exists")) {
                        return Mono.just(ResponseEntity.status(409).body(null)); // 409 Conflict
                    }
                    
                    return Mono.just(ResponseEntity.status(500).build());
                });
    }

    @PutMapping("/{id}")
    public Mono<ResponseEntity<User>> updateUser(@PathVariable String id, @RequestBody User updatedUser) {
        return userService.updateUser(id, updatedUser)
                .map(ResponseEntity::ok)
                .defaultIfEmpty(ResponseEntity.notFound().build())
                .onErrorResume(e -> {
                    log.error("Error updating user: {}", e.getMessage(), e);
                    
                    // Check if it's an email uniqueness error
                    if (e.getMessage() != null && e.getMessage().contains("already exists")) {
                        return Mono.just(ResponseEntity.status(409).body(null)); // 409 Conflict
                    }
                    
                    return Mono.just(ResponseEntity.status(500).build());
                });
    }

    @PatchMapping("/{id}")
    public Mono<ResponseEntity<User>> patchUser(@PathVariable String id, @RequestBody Map<String, Object> updates) {
        return userService.patchUser(id, updates)
                .map(ResponseEntity::ok)
                .defaultIfEmpty(ResponseEntity.notFound().build())
                .onErrorResume(e -> {
                    log.error("Error patching user: {}", e.getMessage(), e);
                    
                    // Check if it's an email uniqueness error
                    if (e.getMessage() != null && e.getMessage().contains("already exists")) {
                        return Mono.just(ResponseEntity.status(409).body(null)); // 409 Conflict
                    }
                    
                    return Mono.just(ResponseEntity.status(500).build());
                });
    }

    @DeleteMapping("/{id}")
    public Mono<ResponseEntity<Void>> deleteUser(@PathVariable String id) {
        return userService.deleteUser(id)
                .thenReturn(ResponseEntity.noContent().build());
    }
    
    @GetMapping("/check-email")
    public Mono<ResponseEntity<Boolean>> isEmailAvailable(@RequestParam String email) {
        return userService.isEmailAvailable(email)
                .map(ResponseEntity::ok);
    }
}