package com.phaseGateTwo.cms.userAuth.exceptions;

public class InvalidOtpException extends RuntimeException {
    public InvalidOtpException() { super("Invalid or expired OTP"); }
}
