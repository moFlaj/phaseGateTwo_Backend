package com.phaseGateTwo.cms.userProfile.services;

import com.phaseGateTwo.cms.userAuth.models.User;
import com.phaseGateTwo.cms.userAuth.repositories.UserRepository;
import com.phaseGateTwo.cms.userProfile.dtos.requests.UpdateProfileDetailsRequest;
import com.phaseGateTwo.cms.userProfile.dtos.responses.ViewUserProfileResponse;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;

@Service
public class UserProfileServices {

    private final UserRepository userRepository;

    public UserProfileServices(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public ViewUserProfileResponse getUserProfileInfo(Authentication authentication) {
       User foundUser = userRepository.findById(getUserId(authentication)).get();
       return new ViewUserProfileResponse(foundUser.getFullName(), foundUser.getPhoneNumber(), foundUser.getEmail());
    }

    private String getUserId(Authentication authentication) {
        return (String) authentication.getPrincipal();
    }

    public ViewUserProfileResponse updateUserProfile(Authentication authentication, UpdateProfileDetailsRequest request) {
        String userId = getUserId(authentication);
        User foundUser = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));

        // Since PUT is full update, overwrite all fields
        foundUser.setFullName(request.getFullName());
        foundUser.setPhoneNumber(request.getPhoneNumber());
        foundUser.setEmail(request.getEmail());

        User updated = userRepository.save(foundUser);
        return new ViewUserProfileResponse(
                updated.getFullName(),
                updated.getPhoneNumber(),
                updated.getEmail()
        );
    }

}
