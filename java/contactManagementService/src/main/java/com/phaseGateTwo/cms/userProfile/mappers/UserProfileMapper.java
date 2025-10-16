package com.phaseGateTwo.cms.userProfile.mappers;

import com.phaseGateTwo.cms.userAuth.models.User;
import com.phaseGateTwo.cms.userProfile.dtos.requests.AddContactRequest;
import com.phaseGateTwo.cms.userProfile.dtos.requests.EditContactRequest;
import com.phaseGateTwo.cms.userProfile.dtos.requests.UpdateProfileDetailsRequest;
import com.phaseGateTwo.cms.userProfile.dtos.responses.*;
import com.phaseGateTwo.cms.userProfile.models.Contact;
import org.springframework.stereotype.Component;

import java.util.*;
import java.util.stream.Collectors;

@Component
public class UserProfileMapper {

    // --- User mappings ---
    public ViewUserProfileResponse toViewUserProfileResponse(User user) {
        return new ViewUserProfileResponse(user.getFullName(), user.getPhoneNumber(), user.getEmail());
    }

    public User applyUpdateProfileDetailsRequestToUser(UpdateProfileDetailsRequest req, User user) {
        user.setFullName(req.getFullName());
        user.setPhoneNumber(req.getPhoneNumber());
        user.setEmail(req.getEmail());
        return user;
    }

    // --- Contact mappings ---
    public Contact fromAddContactRequest(AddContactRequest req, String userId) {
        Contact c = new Contact();
        c.setUserId(userId);
        c.setFullName(req.getFullName());
        c.setPhone(req.getPhone());
        c.setEmail(req.getEmail());
        return c;
    }

    public Contact applyEditContactRequestToContact(EditContactRequest req, Contact contact) {
        contact.setFullName(req.getFullName());
        contact.setPhone(req.getPhone());
        contact.setEmail(req.getEmail());
        return contact;
    }

    public AddContactResponse toAddContactResponse(Contact contact) {
        return new AddContactResponse(contact.getContactId(), contact.getFullName(), contact.getPhone(), contact.getEmail());
    }

    public EditContactResponse toEditContactResponse(Contact contact) {
        return new EditContactResponse(contact.getContactId(), contact.getFullName(), contact.getPhone(), contact.getEmail());
    }

    public ViewContactResponse toViewContactResponse(Contact contact) {
        return new ViewContactResponse(contact.getFullName(), contact.getPhone(), contact.getEmail());
    }

    public List<Map<String, String>> toContactSummaryList(List<Contact> contacts) {
        if (contacts == null) return Collections.emptyList();
        return contacts.stream().map(c -> {
            Map<String, String> m = new HashMap<>();
            m.put("contactId", c.getContactId());
            m.put("fullName", c.getFullName());
            return m;
        }).collect(Collectors.toList());
    }
}
