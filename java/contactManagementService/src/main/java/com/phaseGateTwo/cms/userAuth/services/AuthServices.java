package com.phaseGateTwo.cms.userAuth.services;

import com.phaseGateTwo.cms.userAuth.config.JwtUtil;
import com.phaseGateTwo.cms.userAuth.dtos.requests.OtpValidationRequest;
import com.phaseGateTwo.cms.userAuth.dtos.requests.SignUpRequest;
import com.phaseGateTwo.cms.userAuth.dtos.requests.VerifyUserRequest;
import com.phaseGateTwo.cms.userAuth.dtos.responses.VerifyUserResponse;
import com.phaseGateTwo.cms.userAuth.mappers.AuthMapper;
import com.phaseGateTwo.cms.userAuth.models.Otp;
import com.phaseGateTwo.cms.userAuth.models.User;
import com.phaseGateTwo.cms.userAuth.validators.UserValidator;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthServices {

    private final UserServices userService;
    private final OtpServices otpService;
    private final JwtUtil jwtUtil;
    private final UserValidator validator;

    public VerifyUserResponse verify(VerifyUserRequest req) {
        String phone = req.getPhoneNumber();
        if (userService.existsByPhoneNumber(phone)) {
            Otp otp = otpService.createOtpForLogin(phone);
            return AuthMapper.toVerifyUserResponse(otp);
        }
        return AuthMapper.toVerifyUserResponseNoOtp(phone);
    }

    public VerifyUserResponse signup(SignUpRequest req) {
        validator.assertUserDoesNotExist(req.getPhoneNumber());
        Otp otp = otpService.createOtpForSignup(req);
        return AuthMapper.toVerifyUserResponse(otp);
    }

    public String confirmSignUp(OtpValidationRequest req) {
        Otp otp = otpService.validateAndConsume(req.getPhoneNumber(), req.getOtp());
        User user = AuthMapper.fromOtpToUser(otp);
        User saved = userService.save(user);
        return jwtUtil.generateToken(saved.getUserId(), saved.getPhoneNumber());
    }

    public VerifyUserResponse requestLoginOtp(VerifyUserRequest req) {
        validator.assertUserExists(req.getPhoneNumber());
        Otp otp = otpService.createOtpForLogin(req.getPhoneNumber());
        return AuthMapper.toVerifyUserResponse(otp);
    }

    public String confirmLogin(OtpValidationRequest req) {
        otpService.validateAndConsume(req.getPhoneNumber(), req.getOtp());
        User user = userService.findByPhoneNumber(req.getPhoneNumber())
                .orElseThrow(() -> new RuntimeException("Unexpected: User not found after valid OTP"));
        return jwtUtil.generateToken(user.getUserId(), user.getPhoneNumber());
    }
}
