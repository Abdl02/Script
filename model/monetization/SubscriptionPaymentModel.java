package com.digitinary.dgate.model.monetization;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDate;

/**
 * Subscription payment details model.
 *
 * @author Salah Abu Msameh
 * @since 16/08/2024
 */
@NoArgsConstructor
@AllArgsConstructor
@Data
public class SubscriptionPaymentModel {

    private LocalDate paymentIssueDate;
    private LocalDate paymentValueDate;
    private String amount;
    private String currency;
    private String invoiceNo;
}
