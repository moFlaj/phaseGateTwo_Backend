package com.phaseGateTwo.cms.userProfile.services;

import com.phaseGateTwo.cms.userAuth.models.User;
import com.phaseGateTwo.cms.userAuth.repositories.UserRepository;
import com.phaseGateTwo.cms.userProfile.dtos.requests.UpdateProfileDetailsRequest;
import com.phaseGateTwo.cms.userProfile.dtos.responses.ViewUserProfileResponse;
import com.phaseGateTwo.cms.userProfile.exceptions.UserProfileNotFoundException;
import com.phaseGateTwo.cms.userProfile.mappers.UserProfileMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.core.Authentication;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class UserProfileServicesTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private UserProfileMapper mapper;

    @Mock
    private Authentication authentication;

    @InjectMocks
    private UserProfileServices userProfileServices;

    private User existingUser;
    private ViewUserProfileResponse mappedResponse;
    private UpdateProfileDetailsRequest updateRequest;

    @BeforeEach
    void setUp() {

        existingUser = new User();
        existingUser.setUserId("user123");
        existingUser.setFullName("Jane Doe");
        existingUser.setEmail("jane@example.com");
        existingUser.setPhoneNumber("08011112222");

        mappedResponse = new ViewUserProfileResponse();
        mappedResponse.setFullName(existingUser.getFullName());
        mappedResponse.setEmail(existingUser.getEmail());
        mappedResponse.setPhoneNumber(existingUser.getPhoneNumber());

        updateRequest = new UpdateProfileDetailsRequest();
        updateRequest.setFullName("Janet Doe");
        updateRequest.setEmail("janet@example.com");

        when(authentication.getPrincipal()).thenReturn("user123");
    }

    // ─────────────────────────────────────────────────────────────
    // 1️⃣ getUserProfileInfo tests
    // ─────────────────────────────────────────────────────────────
    @Test
    @DisplayName("getUserProfileInfo should return mapped response when user exists")
    void getUserProfileInfo_ShouldReturnResponse_WhenUserExists() {
        // Arrange
        when(userRepository.findById("user123")).thenReturn(Optional.of(existingUser));
        when(mapper.toViewUserProfileResponse(existingUser)).thenReturn(mappedResponse);

        // Act
        ViewUserProfileResponse response = userProfileServices.getUserProfileInfo(authentication);

        // Assert
        assertThat(response).isNotNull();
        assertThat(response.getFullName()).isEqualTo("Jane Doe");
        assertThat(response.getEmail()).isEqualTo("jane@example.com");

        verify(userRepository).findById("user123");
        verify(mapper).toViewUserProfileResponse(existingUser);
    }

    @Test
    @DisplayName("getUserProfileInfo should throw exception when user not found")
    void getUserProfileInfo_ShouldThrowException_WhenUserNotFound() {
        // Arrange
        when(userRepository.findById("user123")).thenReturn(Optional.empty());

        // Act & Assert
        assertThatThrownBy(() -> userProfileServices.getUserProfileInfo(authentication))
                .isInstanceOf(UserProfileNotFoundException.class)
                .hasMessageContaining("User not found");

        verify(userRepository).findById("user123");
        verifyNoInteractions(mapper);
    }

    // ─────────────────────────────────────────────────────────────
    // 2️⃣ updateUserProfile tests
    // ─────────────────────────────────────────────────────────────
    @Test
    @DisplayName("updateUserProfile should update and return mapped response when user exists")
    void updateUserProfile_ShouldUpdateUser_WhenUserExists() {
        // Arrange
        when(userRepository.findById("user123")).thenReturn(Optional.of(existingUser));
        User updatedUser = new User();
        updatedUser.setUserId("user123");
        updatedUser.setFullName("Janet Doe");
        updatedUser.setEmail("janet@example.com");
        updatedUser.setPhoneNumber("08011112222");

        when(mapper.applyUpdateProfileDetailsRequestToUser(updateRequest, existingUser))
                .thenReturn(updatedUser);
        when(userRepository.save(updatedUser)).thenReturn(updatedUser);
        when(mapper.toViewUserProfileResponse(updatedUser)).thenReturn(mappedResponse);

        // Act
        ViewUserProfileResponse response = userProfileServices.updateUserProfile(authentication, updateRequest);

        // Assert
        assertThat(response).isNotNull();
        verify(userRepository).findById("user123");
        verify(mapper).applyUpdateProfileDetailsRequestToUser(updateRequest, existingUser);
        verify(userRepository).save(updatedUser);
        verify(mapper).toViewUserProfileResponse(updatedUser);
    }

    @Test
    @DisplayName("updateUserProfile should throw exception when user not found")
    void updateUserProfile_ShouldThrowException_WhenUserNotFound() {
        // Arrange
        when(userRepository.findById("user123")).thenReturn(Optional.empty());

        // Act & Assert
        assertThatThrownBy(() -> userProfileServices.updateUserProfile(authentication, updateRequest))
                .isInstanceOf(UserProfileNotFoundException.class)
                .hasMessageContaining("User not found");

        verify(userRepository).findById("user123");
        verifyNoMoreInteractions(userRepository);
        verifyNoInteractions(mapper);
    }
}
