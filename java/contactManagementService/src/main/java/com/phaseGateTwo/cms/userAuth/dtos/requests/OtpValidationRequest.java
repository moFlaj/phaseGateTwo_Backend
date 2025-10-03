package com.phaseGateTwo.cms.userAuth.dtos.requests;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class OtpValidationRequest {
    private String phoneNumber;
    private String otp;
}
