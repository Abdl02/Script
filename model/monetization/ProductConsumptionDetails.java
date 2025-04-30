package com.digitinary.dgate.model.monetization;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.math.BigDecimal;

/**
 * Product details based on the consumption.
 *
 * @author Tala Kafafi
 * @since 07/11/2024
 */

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class ProductConsumptionDetails {

    private Long productId;
    private String productName;
    private Long apiCallsTotal;
    private Long remainingHit;
    private Long consumption;
    private BigDecimal price;
}
