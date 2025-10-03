package com.phaseGateTwo.cms.userAuth.services;

import com.phaseGateTwo.cms.userAuth.config.JwtUtil;
import com.phaseGateTwo.cms.userAuth.dtos.requests.OtpValidationRequest;
import com.phaseGateTwo.cms.userAuth.dtos.requests.SignUpRequest;
import com.phaseGateTwo.cms.userAuth.dtos.requests.VerifyUserRequest;
import com.phaseGateTwo.cms.userAuth.dtos.responses.VerifyUserResponse;
import com.phaseGateTwo.cms.userAuth.exceptions.UserAlreadyExistsException;
import com.phaseGateTwo.cms.userAuth.exceptions.UserNotFoundException;
import com.phaseGateTwo.cms.userAuth.models.Otp;
import com.phaseGateTwo.cms.userAuth.models.User;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthServices {
    private final UserServices userService;
    private final OtpServices otpService;
    private final JwtUtil jwtUtil;

    // Step 1: verify phone — response tells frontend whether to show signup or login
    public VerifyUserResponse verify(VerifyUserRequest req) {
        String phone = req.getPhoneNumber();
        if (userService.existsByPhoneNumber(phone)) {
            // existing user -> create login OTP
            Otp otp = otpService.createOtpForLogin(phone);
            return new VerifyUserResponse(phone, otp.getOtp());
        } else {
            // not registered -> no otp, instruct frontend to show signup page
            return new VerifyUserResponse(phone, null);
        }
    }

    // Step 2: signup form submitted -> store signup info inside OTP doc and return the otp (frontend will show OTP page)
    public VerifyUserResponse signup(SignUpRequest req) {
        String phone = req.getPhoneNumber();
        if (userService.existsByPhoneNumber(phone)) throw new UserAlreadyExistsException(phone);
        Otp otp = otpService.createOtpForSignup(req);
        return new VerifyUserResponse(phone, otp.getOtp());
    }

    // Step 2b: confirm signup with OTP -> create com.phaseGateTwo.cms.userauth.model.User and return JWT
    public String confirmSignUp(OtpValidationRequest req) {
        Otp doc = otpService.validateAndConsume(req.getPhoneNumber(), req.getOtp());
        // doc should contain pending signup info

        User user = new User();
        user.setPhoneNumber(doc.getPhoneNumber());
        user.setFullName(doc.getPendingFullName());
        user.setEmail(doc.getPendingEmail());
        User saved = userService.save(user);
        return jwtUtil.generateToken(saved.getUserId(), saved.getPhoneNumber());
    }

    // Login flow: request login OTP (frontend calls this after verify indicated user exists)
    public VerifyUserResponse requestLoginOtp(VerifyUserRequest req) {
        String phone = req.getPhoneNumber();
        if (!userService.existsByPhoneNumber(phone)) throw new UserNotFoundException(phone);
        Otp otp = otpService.createOtpForLogin(phone);
        return new VerifyUserResponse(phone, otp.getOtp());
    }

    // Confirm login with OTP -> return JWT
    public String confirmLogin(OtpValidationRequest req) {
        Otp doc = otpService.validateAndConsume(req.getPhoneNumber(), req.getOtp());
        User user = userService.findByPhoneNumber(req.getPhoneNumber())
                .orElseThrow(() -> new UserNotFoundException(req.getPhoneNumber()));
        return jwtUtil.generateToken(user.getUserId(), user.getPhoneNumber());
    }

}
