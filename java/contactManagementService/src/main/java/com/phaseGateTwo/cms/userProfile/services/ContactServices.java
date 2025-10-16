package com.phaseGateTwo.cms.userProfile.services;

import com.phaseGateTwo.cms.userProfile.dtos.requests.AddContactRequest;
import com.phaseGateTwo.cms.userProfile.dtos.requests.EditContactRequest;
import com.phaseGateTwo.cms.userProfile.dtos.responses.*;
import com.phaseGateTwo.cms.userProfile.exceptions.ContactNotFoundException;
import com.phaseGateTwo.cms.userProfile.exceptions.DuplicateContactException;
import com.phaseGateTwo.cms.userProfile.exceptions.UnauthorizedContactAccessException;
import com.phaseGateTwo.cms.userProfile.mappers.UserProfileMapper;
import com.phaseGateTwo.cms.userProfile.models.Contact;
import com.phaseGateTwo.cms.userProfile.repositories.ContactsRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.Optional;

@Service
public class ContactServices {

    private final ContactsRepository contactRepository;
    private final UserProfileMapper mapper;

    public ContactServices(ContactsRepository contactRepository, UserProfileMapper mapper) {
        this.contactRepository = contactRepository;
        this.mapper = mapper;
    }

    public ViewUserContactsResponse getAllContactsByUserId(String userId) {
        List<Contact> userContacts = contactRepository.findByUserId(userId);
        List<Map<String, String>> contactsList = mapper.toContactSummaryList(userContacts);
        return new ViewUserContactsResponse(contactsList);
    }

    public EditContactResponse editContact(String userId, String contactId, EditContactRequest request) {
        Contact contact = contactRepository.findById(contactId)
                .orElseThrow(() -> new ContactNotFoundException("Contact not found"));

        if (!contact.getUserId().equals(userId)) {
            throw new UnauthorizedContactAccessException("Unauthorized");
        }

        Contact editedContact = mapper.applyEditContactRequestToContact(request, contact);
        Contact saved = contactRepository.save(editedContact);
        return mapper.toEditContactResponse(saved);
    }

    public AddContactResponse addContact(String userId, AddContactRequest request) {
        Optional<Contact> existing = contactRepository.findByPhoneAndUserId(request.getPhone(), userId);

        if (existing.isPresent()) {
            throw new DuplicateContactException("Contact with this phone number already exists. Send update request to modify.");
        }

        Contact contact = mapper.fromAddContactRequest(request, userId);
        Contact saved = contactRepository.save(contact);
        return mapper.toAddContactResponse(saved);
    }


    public ViewContactResponse getContactById(String contactId, String userId) {
        Optional<Contact> contactOpt = contactRepository.findByContactIdAndUserId(contactId, userId);
        Contact contact = contactOpt.orElseThrow(() -> new ContactNotFoundException("Contact not found"));
        return mapper.toViewContactResponse(contact);
    }

    public DeleteContactResponse deleteContact(String userId, String contactId) {
        Contact contact = contactRepository.findByContactIdAndUserId(contactId, userId)
                .orElseThrow(() -> new ContactNotFoundException("Contact not found"));

        contactRepository.delete(contact);
        return new DeleteContactResponse("Contact deleted successfully");
    }

}
