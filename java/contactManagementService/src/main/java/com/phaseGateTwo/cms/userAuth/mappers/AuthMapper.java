package com.phaseGateTwo.cms.userAuth.mappers;

import com.phaseGateTwo.cms.userAuth.dtos.requests.SignUpRequest;
import com.phaseGateTwo.cms.userAuth.dtos.responses.VerifyUserResponse;
import com.phaseGateTwo.cms.userAuth.models.Otp;
import com.phaseGateTwo.cms.userAuth.models.User;

public class AuthMapper {

    public static User fromOtpToUser(Otp otp) {
        User user = new User();
        user.setPhoneNumber(otp.getPhoneNumber());
        user.setFullName(otp.getPendingFullName());
        user.setEmail(otp.getPendingEmail());
        return user;
    }

    public static VerifyUserResponse toVerifyUserResponse(Otp otp) {
        return new VerifyUserResponse(otp.getPhoneNumber(), otp.getOtp());
    }

    public static VerifyUserResponse toVerifyUserResponseNoOtp(String phoneNumber) {
        return new VerifyUserResponse(phoneNumber, null);
    }

    public static Otp fromSignupRequest(SignUpRequest req, String generatedOtp) {
        Otp otp = new Otp();
        otp.setPhoneNumber(req.getPhoneNumber());
        otp.setOtp(generatedOtp);
        otp.setPendingFullName(req.getFullName());
        otp.setPendingEmail(req.getEmail());
        return otp;
    }
}
