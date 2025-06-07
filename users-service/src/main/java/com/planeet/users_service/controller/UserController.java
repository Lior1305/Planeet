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
public class UserController {

    private static final Logger log = LoggerFactory.getLogger(UserController.class);
    @Autowired
    private UserService userService;

    @GetMapping
    public Flux<User> getAllUsers() {
        log.info("Got a request to bring all users");
        return userService.getAllUsers();
    }

    @GetMapping("/{id}")
    public Mono<ResponseEntity<User>> getUserById(@PathVariable String id) {
        return userService.getUserById(id);
    }

    @PostMapping
    public Mono<ResponseEntity<User>> createUser(@RequestBody User user) {
        return userService.createUser(user)
                .map(ResponseEntity::ok)
                .onErrorResume(e -> {
                    e.printStackTrace();  // ✅ log the real issue
                    return Mono.just(ResponseEntity.status(500).build());
                });
    }

   @PutMapping("/{id}")
   public Mono<User> updateUser(@PathVariable String id, @RequestBody User updatedUser) {
       return userService.updateUser(id, updatedUser);
   }

    @PatchMapping("/{id}")
    public Mono<User> patchUser(@PathVariable String id, @RequestBody Map<String, Object> updates) {
        return userService.patchUser(id, updates);
    }


    @DeleteMapping("/{id}")
    public Mono<Void> deleteUser(@PathVariable String id) {
        return userService.deleteUser(id);
    }
}
