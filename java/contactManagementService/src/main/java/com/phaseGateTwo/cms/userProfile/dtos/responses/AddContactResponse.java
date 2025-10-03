package com.phaseGateTwo.cms.userProfile.dtos.responses;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AddContactResponse {

    private String id;
    private String fullName;
    private String phone;
    private String email;
}