package com.digitinary.dgate.model.apispec;

import com.digitinary.dgate.model.RestrictionType;
import com.digitinary.dgate.model.apispec.policy.ApiPolicyFilter;
import com.digitinary.dgate.model.authenticator.AuthenticatorType;
import com.digitinary.dgate.model.monetization.AssociatedResource;
import com.digitinary.dgate.model.revision.RevisionChangeModel;
import com.digitinary.dgate.model.route.ApiSpecRouteModel;
import com.digitinary.dgate.model.runtimeconfig.RuntimeConfigPublicationModel;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;
import java.util.Set;

/**
 * The main core model.
 * ApiSpec represent the main API specs deployed/expose by the gateway.
 *
 * @author Salah Abu Msameh
 * @since 04/06/2023
 */
@JsonIgnoreProperties(ignoreUnknown = true)
@JsonInclude(JsonInclude.Include.NON_NULL)
@AllArgsConstructor
@NoArgsConstructor
@Builder
@Data
public class ApiSpec {

    private String apiSpecId;
    private String name;
    private String description;
    private String contextPath;
    //private String backendServiceUrl; //  moved to the gateway environment
    private ApiStatus status;
    private ApiType type;
    private ApiStyle style;
    private MetaData metaData;
    private String policyTemplateId;
    private CreationFlag creationFlag;
    private boolean addVersionToContextPath;
    private AuthenticatorType authType;

    private List<ApiPolicyFilter> predicates;
    private Set<ApiPolicyFilter> requestPolicies;
    private Set<ApiPolicyFilter> responsePolicies;
    private List<ApiSpec> oldVersions;
    private Set<ApiSpecRouteModel> apiSpecRoutes;
    private List<RevisionChangeModel> revisions;
    private List<AssociatedResource> associatedResources;
    private List<RuntimeConfigPublicationModel> publications;
    private RestrictionType restriction;
}