package com.phaseGateTwo.cms.userProfile.dtos.responses;

import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ViewContactResponse {
    private String fullName;
    private String phone;
    private String email;
}