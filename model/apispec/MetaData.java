package com.digitinary.dgate.model.apispec;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;
import java.util.Set;

/**
 * API Spec meta data.
 *
 * @author Salah Abu Msameh
 * @since 05/06/2023
 */
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class MetaData {

    private String version;
    private String apiVersionOf;
    private String category;
    private String openApiJson;
    private Set<String> tags;
    private String owner;
    private LocalDateTime createdDateTime;
    private LocalDateTime lastUpdatedDateTime;

    public String getVersion() {
        return version;
    }

    public void setVersion(final String version) {
        this.version = version;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(final String category) {
        this.category = category;
    }

    public Set<String> getTags() {
        return tags;
    }

    public void setTags(final Set<String> tags) {
        this.tags = tags;
    }

    public String getApiVersionOf() {
        return apiVersionOf;
    }

    public void setApiVersionOf(final String apiVersionOf) {
        this.apiVersionOf = apiVersionOf;
    }

    public String getOpenApiJson() {
        return openApiJson;
    }

    public void setOpenApiJson(final String openApiJson) {
        this.openApiJson = openApiJson;
    }

    public String getOwner() {
        return owner;
    }

    public void setOwner(final String owner) {
        this.owner = owner;
    }

    public LocalDateTime getCreatedDateTime() {
        return createdDateTime;
    }

    public void setCreatedDateTime(final LocalDateTime createdDateTime) {
        this.createdDateTime = createdDateTime;
    }

    public LocalDateTime getLastUpdatedDateTime() {
        return lastUpdatedDateTime;
    }

    public void setLastUpdatedDateTime(final LocalDateTime lastUpdatedDateTime) {
        this.lastUpdatedDateTime = lastUpdatedDateTime;
    }
}

