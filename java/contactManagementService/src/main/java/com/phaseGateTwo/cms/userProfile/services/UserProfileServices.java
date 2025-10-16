package com.phaseGateTwo.cms.userProfile.services;

import com.phaseGateTwo.cms.userAuth.models.User;
import com.phaseGateTwo.cms.userAuth.repositories.UserRepository;
import com.phaseGateTwo.cms.userProfile.dtos.requests.UpdateProfileDetailsRequest;
import com.phaseGateTwo.cms.userProfile.dtos.responses.ViewUserProfileResponse;
import com.phaseGateTwo.cms.userProfile.exceptions.UserProfileNotFoundException;
import com.phaseGateTwo.cms.userProfile.mappers.UserProfileMapper;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;

@Service
public class UserProfileServices {

    private final UserRepository userRepository;
    private final UserProfileMapper mapper;

    public UserProfileServices(UserRepository userRepository, UserProfileMapper mapper) {
        this.userRepository = userRepository;
        this.mapper = mapper;
    }

    public ViewUserProfileResponse getUserProfileInfo(Authentication authentication) {
        String userId = getUserId(authentication);
        User foundUser = userRepository.findById(userId)
                .orElseThrow(() -> new UserProfileNotFoundException("User not found"));
        return mapper.toViewUserProfileResponse(foundUser);
    }

    public ViewUserProfileResponse updateUserProfile(Authentication authentication, UpdateProfileDetailsRequest request) {
        String userId = getUserId(authentication);
        User foundUser = userRepository.findById(userId)
                .orElseThrow(() -> new UserProfileNotFoundException("User not found"));


        foundUser = mapper.applyUpdateProfileDetailsRequestToUser(request, foundUser);

        User updated = userRepository.save(foundUser);
        return mapper.toViewUserProfileResponse(updated);
    }

    private String getUserId(Authentication authentication) {
        return (String) authentication.getPrincipal();
    }
}
