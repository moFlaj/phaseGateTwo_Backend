package com.phaseGateTwo.cms.userProfile.dtos.responses;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ViewUserProfileResponse {
    private String fullName;
    private String phoneNumber;
    private String email;
}

