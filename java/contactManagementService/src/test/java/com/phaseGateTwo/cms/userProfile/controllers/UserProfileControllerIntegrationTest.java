package com.phaseGateTwo.cms.userProfile.controllers;

import com.fasterxml.jackson.core.type.TypeReference;
import com.phaseGateTwo.cms.common.BaseIntegrationTest;
import com.phaseGateTwo.cms.userProfile.dtos.requests.UpdateProfileDetailsRequest;
import com.phaseGateTwo.cms.userProfile.dtos.responses.ViewUserProfileResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;



public class UserProfileControllerIntegrationTest extends BaseIntegrationTest {

    private String jwtToken;

    @BeforeEach
    void setup() throws Exception {
        jwtToken = signupAndGetJwt("08012345678", "userprofile@example.com", "John Doe");
    }

    @Test
    @DisplayName("GET /api/profile/view should return user profile successfully")
    void shouldReturnUserProfileInfo() throws Exception {
        // Arrange
        var requestBuilder = MockMvcRequestBuilders.get("/api/profile/view")
                .header("Authorization", "Bearer " + jwtToken)
                .contentType(MediaType.APPLICATION_JSON);

        // Act
        MvcResult result = mockMvc.perform(requestBuilder)
                .andExpect(status().isOk())
                .andReturn();

        // Assert
        ViewUserProfileResponse response = objectMapper.readValue(
                result.getResponse().getContentAsString(),
                new TypeReference<>() {}
        );

        assertThat(response).isNotNull();
        assertThat(response.getEmail()).isEqualTo("userprofile@example.com");
        assertThat(response.getFullName()).isEqualTo("John Doe");
    }

    @Test
    @DisplayName("PUT /api/profile/update should update user profile successfully")
    void shouldUpdateUserProfileInfo() throws Exception {
        // Arrange
        UpdateProfileDetailsRequest updateRequest = new UpdateProfileDetailsRequest();
        updateRequest.setFullName("Updated Name");
        updateRequest.setEmail("updated@example.com");
        updateRequest.setPhoneNumber("08099998888");

        String jsonBody = objectMapper.writeValueAsString(updateRequest);

        var requestBuilder = MockMvcRequestBuilders.put("/api/profile/update")
                .header("Authorization", "Bearer " + jwtToken)
                .contentType(MediaType.APPLICATION_JSON)
                .content(jsonBody);

        // Act
        MvcResult result = mockMvc.perform(requestBuilder)
                .andExpect(status().isOk())
                .andReturn();

        // Assert
        ViewUserProfileResponse response = objectMapper.readValue(
                result.getResponse().getContentAsString(),
                new TypeReference<>() {}
        );

        assertThat(response).isNotNull();
        assertThat(response.getFullName()).isEqualTo("Updated Name");
        assertThat(response.getEmail()).isEqualTo("updated@example.com");
        assertThat(response.getPhoneNumber()).isEqualTo("08099998888");
    }

    @Test
    @DisplayName("GET /api/profile/view should return 404 if user not found")
    void shouldReturn404WhenUserNotFound() throws Exception {
        // Arrange
        // simulate deletion from DB if needed or use a fake JWT with non-existent user id
        String fakeJwt = signupAndGetJwt("08123456789", "ghost@example.com", "Ghost User");
        mongoTemplate.dropCollection("users");


        var requestBuilder = MockMvcRequestBuilders.get("/api/profile/view")
                .header("Authorization", "Bearer " + fakeJwt)
                .contentType(MediaType.APPLICATION_JSON);

        // Act & Assert
        mockMvc.perform(requestBuilder)
                .andExpect(status().isNotFound());
    }
}
