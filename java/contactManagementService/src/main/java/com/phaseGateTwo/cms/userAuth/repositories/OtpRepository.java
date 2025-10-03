package com.phaseGateTwo.cms.userAuth.repositories;


import com.phaseGateTwo.cms.userAuth.models.Otp;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface OtpRepository extends MongoRepository<Otp, String> {
}
