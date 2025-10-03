package com.phaseGateTwo.cms.userAuth.services;

import com.phaseGateTwo.cms.userAuth.dtos.requests.SignUpRequest;
import com.phaseGateTwo.cms.userAuth.exceptions.InvalidOtpException;
import com.phaseGateTwo.cms.userAuth.models.Otp;
import com.phaseGateTwo.cms.userAuth.repositories.OtpRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.Optional;
import java.util.Random;

@Service
@RequiredArgsConstructor
public class OtpServices {
    private final OtpRepository otpRepository;
    private final Random rnd = new Random();

    private String newOtp() { return String.format("%06d", rnd.nextInt(1_000_000)); }

    // generate OTP for login (no pending signup data)
    public Otp createOtpForLogin(String phoneNumber) {
        Otp doc = new Otp();
        doc.setPhoneNumber(phoneNumber);
        doc.setOtp(newOtp());
        doc.setPendingFullName(null);
        doc.setPendingEmail(null);
        return otpRepository.save(doc);
    }

    // generate OTP for signup and store pending signup info in the same doc
    public Otp createOtpForSignup(SignUpRequest request) {
        Otp doc = new Otp();
        doc.setPhoneNumber(request.getPhoneNumber());
        doc.setOtp(newOtp());
        doc.setPendingFullName(request.getFullName());
        doc.setPendingEmail(request.getEmail());
        return otpRepository.save(doc);
    }

    // validate and consume OTP: returns the stored OtpDocument (with pending signup if any) and deletes the doc
    public Otp validateAndConsume(String phoneNumber, String otp) {
        Optional<Otp> opt = otpRepository.findById(phoneNumber);
        if (!opt.isPresent()) throw new InvalidOtpException();
        Otp doc = opt.get();
        if (!doc.getOtp().equals(otp)) throw new InvalidOtpException();
        // consume
        otpRepository.deleteById(phoneNumber);
        return doc;
    }

    // helper to find OTP doc (not consumed)
    public Optional<Otp> findByPhone(String phoneNumber) {
        return otpRepository.findById(phoneNumber);
    }
}
