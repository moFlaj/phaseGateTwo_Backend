package com.phaseGateTwo.cms.userProfile.dtos.requests;

import lombok.Data;


@Data
public class UpdateProfileDetailsRequest {
    private String fullName;
    private String phoneNumber;
    private String email;
}
