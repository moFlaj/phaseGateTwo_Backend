package com.phaseGateTwo.cms.userAuth.dtos.requests;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class VerifyUserRequest {

    @Pattern(regexp = "\\d+", message = "Must contain only numbers")
    @NotBlank(message = "Name must not be blank")
    @Size(min = 8, max = 15, message = "Phone number must be between 8 and 15 digits")
    private String phoneNumber;
}

