package com.phaseGateTwo.cms.userAuth.exceptions;

public class UserAlreadyExistsException extends RuntimeException {
    public UserAlreadyExistsException(String phone) { super("User already exists"); }
}
