package com.phaseGateTwo.cms.userAuth.dtos.requests;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SignUpRequest {
    @Pattern(regexp = "\\d+", message = "Must contain only numbers")
    @NotBlank(message = "This is a required field")
    @Size(min = 8, max = 15, message = "Phone number must be between 8 and 15 digits")
    private String phoneNumber;

    @NotBlank(message = "This is a required field")
    @Pattern(
            regexp = "^(\\S+\\s+\\S+)(\\s+\\S+)?$",
            message = "Full name must contain 2 or 3 words"
    )
    private String fullName;
    @NotBlank(message = "This is a required field")
    @Email(message = "Invalid email format")
    private String email;
}
