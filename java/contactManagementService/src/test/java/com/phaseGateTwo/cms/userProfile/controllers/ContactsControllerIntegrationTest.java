package com.phaseGateTwo.cms.userProfile.controllers;

import com.phaseGateTwo.cms.common.BaseIntegrationTest;
import com.phaseGateTwo.cms.userProfile.dtos.requests.AddContactRequest;
import com.phaseGateTwo.cms.userProfile.dtos.requests.EditContactRequest;
import com.phaseGateTwo.cms.userProfile.dtos.responses.*;
import com.phaseGateTwo.cms.userProfile.mappers.UserProfileMapper;
import com.phaseGateTwo.cms.userProfile.models.Contact;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

public class ContactsControllerIntegrationTest extends BaseIntegrationTest {

    @Autowired
    private UserProfileMapper mapper;

    private String jwt;

    @BeforeEach
    void setupUser() throws Exception {
        // Clean contacts collection before each test
        mongoTemplate.dropCollection("contacts");

        // Sign up a user and get JWT
        jwt = signupAndGetJwt("08123456789", "user@example.com", "Test User");
    }

    @Test
    void shouldAddContactSuccessfully() throws Exception {
        AddContactRequest req = new AddContactRequest();
        req.setFullName("Bob");
        req.setPhone("09002223344");
        req.setEmail("bob@example.com");

        String response = mockMvc.perform(MockMvcRequestBuilders.post("/api/contacts/add")
                        .header("Authorization", "Bearer " + jwt)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(req)))
                .andExpect(status().isOk())
                .andReturn().getResponse().getContentAsString();

        AddContactResponse added = objectMapper.readValue(response, AddContactResponse.class);
        assertThat(added.getFullName()).isEqualTo("Bob");
        assertThat(added.getPhone()).isEqualTo("09002223344");
        assertThat(added.getEmail()).isEqualTo("bob@example.com");
        assertThat(added.getId()).isNotBlank();
    }

    @Test
    void shouldHandleDuplicateContact() throws Exception {
        // Add a contact first
        AddContactRequest req1 = new AddContactRequest();
        req1.setFullName("Alice");
        req1.setPhone("0911000111");
        req1.setEmail("alice@example.com");

        mockMvc.perform(MockMvcRequestBuilders.post("/api/contacts/add")
                        .header("Authorization", "Bearer " + jwt)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(req1)))
                .andExpect(status().isOk());

        // Try adding duplicate phone
        AddContactRequest req2 = new AddContactRequest();
        req2.setFullName("Alice Duplicate");
        req2.setPhone("0911000111"); // same phone
        req2.setEmail("alice.dup@example.com");

        String errorResponse = mockMvc.perform(MockMvcRequestBuilders.post("/api/contacts/add")
                        .header("Authorization", "Bearer " + jwt)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(req2)))
                .andExpect(status().isConflict())
                .andReturn()
                .getResponse()
                .getContentAsString();

        assertThat(errorResponse).contains("already exists");


        Contact existing = mongoTemplate.findAll(Contact.class, "contacts").getFirst();

        EditContactRequest editReq = new EditContactRequest();
        editReq.setFullName("Alice Updated");
        editReq.setPhone("0911000111");
        editReq.setEmail("alice.updated@example.com");

        String updateResp = mockMvc.perform(MockMvcRequestBuilders.put("/api/contacts/" + existing.getContactId() + "/edit")
                        .header("Authorization", "Bearer " + jwt)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(editReq)))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        EditContactResponse updated = objectMapper.readValue(updateResp, EditContactResponse.class);
        assertThat(updated.getFullName()).isEqualTo("Alice Updated");
        assertThat(updated.getEmail()).isEqualTo("alice.updated@example.com");
    }

    @Test
    void shouldDeleteContactSuccessfully() throws Exception {
        // Add a contact
        AddContactRequest req = new AddContactRequest();
        req.setFullName("Charlie");
        req.setPhone("0922000222");
        req.setEmail("charlie@example.com");

        String addResp = mockMvc.perform(MockMvcRequestBuilders.post("/api/contacts/add")
                        .header("Authorization", "Bearer " + jwt)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(req)))
                .andExpect(status().isOk())
                .andReturn().getResponse().getContentAsString();

        AddContactResponse added = objectMapper.readValue(addResp, AddContactResponse.class);

        // Delete it
        String deleteResp = mockMvc.perform(MockMvcRequestBuilders.delete("/api/contacts/" + added.getId())
                        .header("Authorization", "Bearer " + jwt)
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andReturn().getResponse().getContentAsString();

        DeleteContactResponse delResponse = objectMapper.readValue(deleteResp, DeleteContactResponse.class);
        assertThat(delResponse.getMessage()).contains("deleted successfully");
    }

    @Test
    void shouldReturn404WhenDeletingNonExistentContact() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.delete("/api/contacts/nonexistent123")
                        .header("Authorization", "Bearer " + jwt)
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isNotFound());
    }

    @Test
    void shouldGetAllContactsForUser() throws Exception {
        // Add first contact via endpoint
        AddContactRequest req1 = new AddContactRequest();
        req1.setFullName("Alice");
        req1.setPhone("0911000111");
        req1.setEmail("alice@example.com");

        mockMvc.perform(MockMvcRequestBuilders.post("/api/contacts/add")
                        .header("Authorization", "Bearer " + jwt)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(req1)))
                .andExpect(status().isOk());

        // Add second contact via endpoint
        AddContactRequest req2 = new AddContactRequest();
        req2.setFullName("Charlie");
        req2.setPhone("0922000222");
        req2.setEmail("charlie@example.com");

        mockMvc.perform(MockMvcRequestBuilders.post("/api/contacts/add")
                        .header("Authorization", "Bearer " + jwt)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(req2)))
                .andExpect(status().isOk());

        // Now get all contacts for user
        String response = mockMvc.perform(MockMvcRequestBuilders.get("/api/contacts/all")
                        .header("Authorization", "Bearer " + jwt)
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andReturn().getResponse().getContentAsString();

        ViewUserContactsResponse result = objectMapper.readValue(response, ViewUserContactsResponse.class);
        assertThat(result.getContactNames()).isNotEmpty();
        assertThat(result.getContactNames().size()).isGreaterThanOrEqualTo(2);
    }


    @Test
    void shouldEditContactSuccessfully() throws Exception {
        AddContactRequest addReq = new AddContactRequest();
        addReq.setFullName("Dave");
        addReq.setPhone("0933000333");
        addReq.setEmail("dave@example.com");

        String addResp = mockMvc.perform(MockMvcRequestBuilders.post("/api/contacts/add")
                        .header("Authorization", "Bearer " + jwt)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(addReq)))
                .andExpect(status().isOk())
                .andReturn().getResponse().getContentAsString();

        AddContactResponse added = objectMapper.readValue(addResp, AddContactResponse.class);

        EditContactRequest editReq = new EditContactRequest();
        editReq.setFullName("David Updated");
        editReq.setPhone("0933111444");
        editReq.setEmail("david.updated@example.com");

        String editResp = mockMvc.perform(MockMvcRequestBuilders.put("/api/contacts/" + added.getId() + "/edit")
                        .header("Authorization", "Bearer " + jwt)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(editReq)))
                .andExpect(status().isOk())
                .andReturn().getResponse().getContentAsString();

        EditContactResponse edited = objectMapper.readValue(editResp, EditContactResponse.class);
        assertThat(edited.getFullName()).isEqualTo("David Updated");
        assertThat(edited.getPhone()).isEqualTo("0933111444");
        assertThat(edited.getEmail()).isEqualTo("david.updated@example.com");
    }

    @Test
    void shouldGetSpecificContactById() throws Exception {
        AddContactRequest addReq = new AddContactRequest();
        addReq.setFullName("Eve");
        addReq.setPhone("0944000444");
        addReq.setEmail("eve@example.com");

        String addResp = mockMvc.perform(MockMvcRequestBuilders.post("/api/contacts/add")
                        .header("Authorization", "Bearer " + jwt)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(addReq)))
                .andExpect(status().isOk())
                .andReturn().getResponse().getContentAsString();

        AddContactResponse added = objectMapper.readValue(addResp, AddContactResponse.class);

        String viewResp = mockMvc.perform(MockMvcRequestBuilders.get("/api/contacts/" + added.getId())
                        .header("Authorization", "Bearer " + jwt)
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andReturn().getResponse().getContentAsString();

        ViewContactResponse contact = objectMapper.readValue(viewResp, ViewContactResponse.class);
        assertThat(contact.getFullName()).isEqualTo("Eve");
        assertThat(contact.getPhone()).isEqualTo("0944000444");
        assertThat(contact.getEmail()).isEqualTo("eve@example.com");
    }

    @Test
    void shouldReturn404WhenContactNotFound() throws Exception {
        String fakeContactId = "nonexistent123";

        mockMvc.perform(MockMvcRequestBuilders.get("/api/contacts/" + fakeContactId)
                        .header("Authorization", "Bearer " + jwt)
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isNotFound());
    }
}
