package com.digitinary.dgate.model.monetization;

import com.digitinary.dgate.model.RestrictionType;
import com.digitinary.dgate.model.consumer.ProjectModel;
import com.digitinary.dgate.model.runtimeconfig.RuntimeConfigPublicationModel;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.time.LocalDate;
import java.util.List;
import java.util.Set;

/**
 * Subscription model. a subscription representing the info for a user usage contract details of an api plan.
 *
 * @author Salah Abu Msameh
 * @since 12/05/2024
 */
@JsonIgnoreProperties(ignoreUnknown = true)
@JsonInclude(JsonInclude.Include.NON_NULL)
@Setter
@Getter
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class SubscriptionModel {

    private Long subscriptionId;
    private ProjectModel project;
    private SubscriptionStatus status;
    private SubscriptionRenewalType renewalType;
    private SubscriptionPeriodOption subscriptionPeriod;
    private boolean trial;
    private PlanModel plan;
    private List<SubscriptionConsumptionRecord> subscriptionConsumptionRecord;
    private List<RuntimeConfigPublicationModel> publications;
    private RestrictionType restriction;
    private Source source;

    // Subscription tracking fields
    private LocalDate startDate;
    private LocalDate endDate;
    private LocalDate nextBillingDate;
    private LocalDate lastBillingDate;
    private String nextBillingAmount;
    private String lastBillingAmount;
    private LocalDate lastRenewalDate;
    private LocalDate nextRenewalDate;
    private LocalDate cancellationDate;

    // Payment details
    private String paymentMethod;
    private Set<SubscriptionPaymentModel> payments;
}
