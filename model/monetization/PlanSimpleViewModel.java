package com.digitinary.dgate.model.monetization;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Data;
import java.util.Set;

/**
 * PlanSimpleViewModel class.
 *
 * @author Raad khatatbeh
 * @since 20/10/2024
 */
@JsonIgnoreProperties(ignoreUnknown = true)
@JsonInclude(JsonInclude.Include.NON_NULL)
@Data
public class PlanSimpleViewModel {

    private Long planId;
    private String name;
    private String desc;
    private Set<SubscriptionPeriodOption> subscriptionPeriodOptions;
    private boolean sandboxPlan;
    private PlanDefinitionType definitionType;

}