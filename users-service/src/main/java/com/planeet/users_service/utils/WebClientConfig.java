package com.planeet.users_service.utils;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class WebClientConfig {

    private  final Logger log = LoggerFactory.getLogger(WebClientConfig.class);

    @Value("${outing.profile-service.base-url}")
    private String outingProfileBaseUrl;

    @Bean
    public WebClient webClient(WebClient.Builder builder) {
        log.info("Creating WebClient with base URL: {}", outingProfileBaseUrl);

        if (outingProfileBaseUrl == null || outingProfileBaseUrl.isEmpty()) {
            log.error("Base URL is null or empty! Check your application.properties");
            throw new IllegalStateException("outing.profile-service.base-url property is not set");
        }

        return builder
                .baseUrl(outingProfileBaseUrl)
                .build();
    }
}