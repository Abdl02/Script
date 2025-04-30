package com.digitinary.dgate.model.apispec.policy;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.time.LocalDateTime;
import java.util.Map;

/**
 * Api policy filter model.
 *
 * @author Salah Abu Msameh
 * @since 13/01/2024
 */
@Setter
@Getter
@Builder
@AllArgsConstructor
@NoArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiPolicyFilter {

    private Long policyDefinitionId;
    private Map<String, String> args;
    private HttpExchange httpExchange;
    private ExchangePolicyName policyName;
    private String  policyDescription;
    private Long order;
    private LocalDateTime createDate;
    private LocalDateTime lastUpdate;
}
