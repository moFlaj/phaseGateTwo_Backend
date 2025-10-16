package com.phaseGateTwo.cms.userAuth.validators;

import com.phaseGateTwo.cms.userAuth.exceptions.UserAlreadyExistsException;
import com.phaseGateTwo.cms.userAuth.exceptions.UserNotFoundException;
import com.phaseGateTwo.cms.userAuth.services.UserServices;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class UserValidator {

    private final UserServices userServices;

    public void assertUserExists(String phoneNumber) {
        if (!userServices.existsByPhoneNumber(phoneNumber)) {
            throw new UserNotFoundException(phoneNumber);
        }
    }

    public void assertUserDoesNotExist(String phoneNumber) {
        if (userServices.existsByPhoneNumber(phoneNumber)) {
            throw new UserAlreadyExistsException(phoneNumber);
        }
    }
}
