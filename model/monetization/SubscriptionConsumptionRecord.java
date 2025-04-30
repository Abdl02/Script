package com.digitinary.dgate.model.monetization;

import com.digitinary.dgate.model.env.EnvironmentType;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;
import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Consumer subscription consumption model class.
 *
 * @author Salah Abu Msameh
 * @since 09/05/2024
 */
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
@JsonInclude(JsonInclude.Include.NON_NULL)
@Builder
@ToString
public class SubscriptionConsumptionRecord implements Serializable {

    private String envId;
    private EnvironmentType envType;
    private String envName;

    private String consumerKey;
    private Long planId;
    private Long projectId;
    private Long subscriptionId;
    private Long productId;

    private Map<Long,Long> productsConsumptions = new HashMap<>();
    private List<ProductConsumptionDetails> productsConsumptionsDetails;
    private Boolean resetFlag = Boolean.FALSE;
    private Long consumptionPeriod;
    private LocalDateTime lastApiCall = LocalDateTime.now();
}