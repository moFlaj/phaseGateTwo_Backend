package com.phaseGateTwo.cms.userAuth.exceptions;

public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(String phone) { super("User not found: " + phone); }
}
