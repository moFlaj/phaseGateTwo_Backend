package com.phaseGateTwo.cms.userProfile.services;

import com.phaseGateTwo.cms.userProfile.dtos.requests.AddContactRequest;
import com.phaseGateTwo.cms.userProfile.dtos.requests.EditContactRequest;
import com.phaseGateTwo.cms.userProfile.dtos.responses.AddContactResponse;
import com.phaseGateTwo.cms.userProfile.dtos.responses.EditContactResponse;
import com.phaseGateTwo.cms.userProfile.dtos.responses.ViewContactResponse;
import com.phaseGateTwo.cms.userProfile.dtos.responses.ViewUserContactsResponse;
import com.phaseGateTwo.cms.userProfile.models.Contact;
import com.phaseGateTwo.cms.userProfile.repositories.ContactsRepository;
import org.springframework.stereotype.Service;

import java.util.*;


@Service
public class ContactServices {

    private final ContactsRepository contactRepository;

    public ContactServices(ContactsRepository contactRepository) {
        this.contactRepository = contactRepository;
    }

    public ViewUserContactsResponse getAllContactsByUserId(String userId) {
        List<Contact> userContacts = contactRepository.findByUserId(userId);

        List<Map<String, String>> contactsList = new ArrayList<>();

        for (Contact c : userContacts) {
            Map<String, String> contactMap = new HashMap<>();
            contactMap.put("contactId", c.getContactId());
            contactMap.put("fullName", c.getFullName());
            contactsList.add(contactMap);
        }

        return new ViewUserContactsResponse(contactsList);
    }

    public EditContactResponse editContact(String userId, String contactId, EditContactRequest request) {
        // Fetch contact and ensure it belongs to this user
        Contact contact = contactRepository.findById(contactId)
                .orElseThrow(() -> new RuntimeException("Contact not found"));

        if (!contact.getUserId().equals(userId)) {
            throw new RuntimeException("Unauthorized");
        }

        // Update fields
        contact.setFullName(request.getFullName());
        contact.setPhone(request.getPhone());
        contact.setEmail(request.getEmail());

        // Save changes
        contactRepository.save(contact);

        return new EditContactResponse(
                contact.getContactId(),
                contact.getFullName(),
                contact.getPhone(),
                contact.getEmail()
        );
    }

    public AddContactResponse addContact(String userId, AddContactRequest request) {
        Contact contact = new Contact();
        contact.setUserId(userId);
        contact.setFullName(request.getFullName());
        contact.setPhone(request.getPhone());
        contact.setEmail(request.getEmail());

        contactRepository.save(contact);

        return new AddContactResponse(
                contact.getContactId(),
                contact.getFullName(),
                contact.getPhone(),
                contact.getEmail()
        );
    }

    // Fetch single contact by ID
    public ViewContactResponse getContactById(String contactId, String userId) {
        Optional<Contact> contactOpt = contactRepository.findByContactIdAndUserId(contactId, userId);
        if (!contactOpt.isPresent()) {
            throw new RuntimeException("Contact not found");
        }
        Contact contact = contactOpt.get();
        return new ViewContactResponse(contact.getFullName(), contact.getPhone(), contact.getEmail());
    }

}
