package com.phaseGateTwo.cms.userProfile.dtos.requests;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;


@Data
@NoArgsConstructor
@AllArgsConstructor
public class UpdateProfileDetailsRequest {
    private String fullName;
    private String phoneNumber;
    private String email;
}
