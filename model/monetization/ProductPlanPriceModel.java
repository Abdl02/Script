package com.digitinary.dgate.model.monetization;

import com.digitinary.dgate.model.TimeUnit;
import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Data;
import java.math.BigDecimal;
import java.util.Set;

/**
 * This class represents a product plan price. A product will have a list of prices for each different plan.
 *
 * @author Salah Abu Msameh
 * @since 29/09/2024
 */
@Data
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ProductPlanPriceModel {

    private Long id;
    private ProductSimpleViewModel product;
    private PlanSimpleViewModel plan;
    private String planName;
    private Set<SubscriptionPeriodOption> subscriptionPeriodOptions;
    private Set<SubscriptionRenewalType> renewalTypeOptions;
    private ApiPricingType priceType;
    private BigDecimal monthlyPrice;
    private BigDecimal yearlyPrice;
    private BigDecimal lifetimePrice;
    private Long apiCallsQuota;
    private TimeUnit timeUnit;
    private Set<String> missingProductNames;
}
