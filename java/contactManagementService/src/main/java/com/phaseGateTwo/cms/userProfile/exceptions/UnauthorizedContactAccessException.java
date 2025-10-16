package com.phaseGateTwo.cms.userProfile.exceptions;

public class UnauthorizedContactAccessException extends RuntimeException {
    public UnauthorizedContactAccessException(String message) {
        super(message);
    }
}
