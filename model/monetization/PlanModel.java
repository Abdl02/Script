package com.digitinary.dgate.model.monetization;

import com.digitinary.dgate.model.RestrictionType;
import com.digitinary.dgate.model.runtimeconfig.RuntimeConfigPublicationModel;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Set;

/**
 * Monetization plan model.
 *
 * @author Salah Abu Msameh
 * @since 08/05/2024
 */
@JsonIgnoreProperties(ignoreUnknown = true)
@JsonInclude(JsonInclude.Include.NON_NULL)
@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class PlanModel {

    private Long planId;
    private PlanDefinitionType definitionType;
    private String name;
    private String desc;
    private boolean premium;

    //Products and Prices
    private Set<ProductPlanPriceModel> productPlanPrices;

    //Pricing details
    private ApiPricingType priceType;
    private PlanStatus planStatus;

    private Set<SubscriptionRenewalType> renewalTypeOptions;
    private Set<SubscriptionPeriodOption> subscriptionPeriodOptions;
    private List<AssociatedResource> associatedResources;
    private List<RuntimeConfigPublicationModel> publications;
    private LocalDateTime createAt;
    private LocalDateTime lastUpdateAt;
    private RestrictionType restriction;
}
