package com.phaseGateTwo.cms.userProfile.controllers;


import com.phaseGateTwo.cms.userProfile.dtos.requests.UpdateProfileDetailsRequest;
import com.phaseGateTwo.cms.userProfile.dtos.responses.ViewUserProfileResponse;

import com.phaseGateTwo.cms.userProfile.services.UserProfileServices;
import jakarta.validation.Valid;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/profile")
public class UserProfileController {

    private final UserProfileServices services;

    public UserProfileController(UserProfileServices services){
        this.services = services;
    }

    @GetMapping("/view")
    public ViewUserProfileResponse viewProfile(Authentication authentication) {
        return services.getUserProfileInfo(authentication);
    }

    @PutMapping("/update")
    public ViewUserProfileResponse editProfile(Authentication authentication, @Valid @RequestBody UpdateProfileDetailsRequest request) {
        return services.updateUserProfile(authentication, request);
    }


}
