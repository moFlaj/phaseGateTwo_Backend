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
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.*;

import java.util.*;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

public class ContactServicesTest {

    @Mock
    private ContactsRepository contactRepository;

    @Mock
    private UserProfileMapper mapper;

    @InjectMocks
    private ContactServices contactServices;

    private String userId;
    private Contact contact;

    @BeforeEach
    void setup() {
        MockitoAnnotations.openMocks(this);
        userId = "user123";

        contact = new Contact();
        contact.setContactId("contact123");
        contact.setFullName("Alice");
        contact.setPhone("0911000111");
        contact.setEmail("alice@example.com");
        contact.setUserId(userId);
    }

    // --- getAllContactsByUserId ---
    @Test
    void shouldReturnAllContactsForUser() {
        List<Contact> contacts = List.of(contact);
        when(contactRepository.findByUserId(userId)).thenReturn(contacts);

        List<Map<String, String>> mappedList = List.of(Map.of("contactId", "contact123", "fullName", "Alice"));
        when(mapper.toContactSummaryList(contacts)).thenReturn(mappedList);

        ViewUserContactsResponse result = contactServices.getAllContactsByUserId(userId);

        assertThat(result.getContactNames()).hasSize(1);
        assertThat(result.getContactNames().get(0).get("contactId")).isEqualTo("contact123");
        verify(contactRepository).findByUserId(userId);
        verify(mapper).toContactSummaryList(contacts);
    }

    // --- editContact ---
    @Test
    void shouldEditContactSuccessfully() {
        EditContactRequest req = new EditContactRequest();
        req.setFullName("Alice Updated");
        req.setPhone("0999999999");
        req.setEmail("alice.updated@example.com");

        when(contactRepository.findById("contact123")).thenReturn(Optional.of(contact));
        Contact updatedContact = new Contact();
        updatedContact.setContactId(contact.getContactId());
        updatedContact.setUserId(contact.getUserId());
        updatedContact.setFullName(req.getFullName());
        updatedContact.setPhone(req.getPhone());
        updatedContact.setEmail(req.getEmail());

        when(mapper.applyEditContactRequestToContact(req, contact)).thenReturn(updatedContact);
        when(contactRepository.save(updatedContact)).thenReturn(updatedContact);
        when(mapper.toEditContactResponse(updatedContact)).thenReturn(
                new EditContactResponse(updatedContact.getContactId(), updatedContact.getFullName(), updatedContact.getPhone(), updatedContact.getEmail())
        );

        EditContactResponse resp = contactServices.editContact(userId, "contact123", req);

        assertEquals("Alice Updated", resp.getFullName());
        assertEquals("0999999999", resp.getPhone());
        assertEquals("alice.updated@example.com", resp.getEmail());
    }

    @Test
    void editContact_shouldThrowNotFoundIfContactDoesNotExist() {
        when(contactRepository.findById("contact123")).thenReturn(Optional.empty());
        EditContactRequest req = new EditContactRequest();

        assertThrows(ContactNotFoundException.class, () -> contactServices.editContact(userId, "contact123", req));
    }

    @Test
    void editContact_shouldThrowUnauthorizedIfUserMismatch() {
        Contact otherContact = new Contact();
        otherContact.setContactId("contact123");
        otherContact.setUserId("otherUser");

        when(contactRepository.findById("contact123")).thenReturn(Optional.of(otherContact));
        EditContactRequest req = new EditContactRequest();

        assertThrows(UnauthorizedContactAccessException.class,
                () -> contactServices.editContact(userId, "contact123", req));
    }

    // --- addContact ---
    @Test
    void shouldAddNewContactSuccessfully() {
        AddContactRequest req = new AddContactRequest();
        req.setFullName("Bob");
        req.setPhone("0922000222");
        req.setEmail("bob@example.com");

        when(contactRepository.findByPhoneAndUserId("0922000222", userId)).thenReturn(Optional.empty());
        Contact contactToSave = new Contact();
        when(mapper.fromAddContactRequest(req, userId)).thenReturn(contactToSave);
        Contact savedContact = new Contact();
        savedContact.setContactId("c1");
        savedContact.setFullName("Bob");
        savedContact.setPhone("0922000222");
        savedContact.setEmail("bob@example.com");
        when(contactRepository.save(contactToSave)).thenReturn(savedContact);
        when(mapper.toAddContactResponse(savedContact)).thenReturn(new AddContactResponse(savedContact.getContactId(), savedContact.getFullName(), savedContact.getPhone(), savedContact.getEmail()));

        AddContactResponse result = contactServices.addContact(userId, req);
        assertNotNull(result);
        assertEquals("Bob", result.getFullName());
    }

    @Test
    void addContact_shouldThrowDuplicateContactExceptionIfExists() {
        AddContactRequest req = new AddContactRequest();
        req.setFullName("Bob");
        req.setPhone("0922000222");
        req.setEmail("bob@example.com");

        when(contactRepository.findByPhoneAndUserId("0922000222", userId))
                .thenReturn(Optional.of(contact));

        DuplicateContactException thrown = assertThrows(
                DuplicateContactException.class,
                () -> contactServices.addContact(userId, req)
        );

        assertThat(thrown.getMessage())
                .contains("already exists");
    }

    // --- getContactById ---
    @Test
    void shouldReturnContactById() {
        when(contactRepository.findByContactIdAndUserId("contact123", userId)).thenReturn(Optional.of(contact));
        when(mapper.toViewContactResponse(contact)).thenReturn(new ViewContactResponse(contact.getFullName(), contact.getPhone(), contact.getEmail()));

        ViewContactResponse resp = contactServices.getContactById("contact123", userId);
        assertEquals("Alice", resp.getFullName());
        assertEquals("0911000111", resp.getPhone());
    }

    @Test
    void getContactById_shouldThrowNotFound() {
        when(contactRepository.findByContactIdAndUserId("contact123", userId)).thenReturn(Optional.empty());
        assertThrows(ContactNotFoundException.class, () -> contactServices.getContactById("contact123", userId));
    }

    // --- deleteContact ---
    @Test
    void shouldDeleteContactSuccessfully() {
        when(contactRepository.findByContactIdAndUserId("contact123", userId)).thenReturn(Optional.of(contact));
        DeleteContactResponse response = contactServices.deleteContact(userId, "contact123");

        assertThat(response.getMessage()).contains("deleted successfully");
        verify(contactRepository).delete(contact);
    }

    @Test
    void deleteContact_shouldThrowIfNotFound() {
        when(contactRepository.findByContactIdAndUserId("contact123", userId)).thenReturn(Optional.empty());
        assertThrows(RuntimeException.class, () -> contactServices.deleteContact(userId, "contact123"));
    }

}
