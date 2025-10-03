package com.phaseGateTwo.cms.userAuth.controllers;


import com.phaseGateTwo.cms.userAuth.dtos.requests.OtpValidationRequest;
import com.phaseGateTwo.cms.userAuth.dtos.requests.SignUpRequest;
import com.phaseGateTwo.cms.userAuth.dtos.requests.VerifyUserRequest;
import com.phaseGateTwo.cms.userAuth.dtos.responses.VerifyUserResponse;
import com.phaseGateTwo.cms.userAuth.services.AuthServices;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;


@RestController
@RequestMapping("/api/auth")

public class AuthController {

    private final AuthServices authService;

    public AuthController(AuthServices authService) {
        this.authService = authService;
    }

    // initial verify
    @PostMapping("/verify")
    public VerifyUserResponse verify(@Valid @RequestBody VerifyUserRequest request) {
        return authService.verify(request);
    }

    // user submits sign up form -> returns OTP in response (backend stored signup info in OTP doc)
    @PostMapping("/signup")
    public VerifyUserResponse signup(@Valid @RequestBody SignUpRequest request) {
        return authService.signup(request);
    }

    // user confirms signup using OTP -> returns JWT
    @PostMapping("/signup/confirm")
    public String confirmSignUp(@Valid @RequestBody OtpValidationRequest request) {
        return authService.confirmSignUp(request);
    }

//    // request login otp (for existing users)
//    @PostMapping("/login/request-otp")
//    public VerifyUserResponse requestLoginOtp(@Valid @RequestBody VerifyUserRequest request) {
//        return authService.requestLoginOtp(request);
//    }

    // confirm login otp -> returns JWT
    @PostMapping("/login/confirm")
    public String confirmLogin(@Valid @RequestBody OtpValidationRequest request) {
        return authService.confirmLogin(request);
    }


}
