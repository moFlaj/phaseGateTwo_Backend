package com.phaseGateTwo.cms.userProfile.repositories;


import com.phaseGateTwo.cms.userProfile.models.Contact;
import org.springframework.data.mongodb.repository.MongoRepository;
import java.util.List;
import java.util.Optional;

public interface ContactsRepository extends MongoRepository<Contact, String> {
    List<Contact> findByUserId(String userId);
    // Fetch a specific contact by its ID and the user ID
    Optional<Contact> findByContactIdAndUserId(String id, String userId);
    Optional<Contact> findByPhoneAndUserId(String phone, String userId);


}
