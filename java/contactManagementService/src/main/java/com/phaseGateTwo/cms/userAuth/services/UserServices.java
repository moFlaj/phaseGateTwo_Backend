package com.phaseGateTwo.cms.userAuth.services;

import com.phaseGateTwo.cms.userAuth.models.User;
import com.phaseGateTwo.cms.userAuth.repositories.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
@RequiredArgsConstructor
public class UserServices {
    private final UserRepository userRepository;

    public boolean existsByPhoneNumber(String phoneNumber) {
        return userRepository.existsByPhoneNumber(phoneNumber);
    }

    public Optional<User> findByPhoneNumber(String phoneNumber) {
        return userRepository.findByPhoneNumber(phoneNumber);
    }

    public User save(User user) { return userRepository.save(user); }
}
