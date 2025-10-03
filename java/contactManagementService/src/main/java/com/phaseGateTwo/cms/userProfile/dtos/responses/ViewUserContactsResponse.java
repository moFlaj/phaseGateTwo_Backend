package com.phaseGateTwo.cms.userProfile.dtos.responses;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ViewUserContactsResponse {
    private List<Map<String, String>> contactNames;
}