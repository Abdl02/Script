package com.digitinary.dgate.model.monetization;

import com.digitinary.dgate.exception.BadRequestException;
import com.digitinary.dgate.exception.ErrorCode;
import com.fasterxml.jackson.annotation.JsonCreator;

/**
 * class docs.
 *
 * @author Salah Abu Msameh
 * @since 08/05/2024
 */
public enum ApiPricingType {

    USAGE_BASED_CHARGES, FIXED_QUOTA_CHARGES;

    /**
     * from value.
     *
     * @param apiPricingType             apiPricingType
     * @return apiPricingType      apiPricingType
     * @throws BadRequestException BadRequestException
     */
    @JsonCreator
    public static ApiPricingType fromValue(final String apiPricingType) {

        if (apiPricingType == null || apiPricingType.isEmpty()) {
            throw new BadRequestException(ErrorCode.FIELD_ENUM_IS_EMPTY, apiPricingType);
        }

        try {
            return ApiPricingType.valueOf(apiPricingType);
        } catch (IllegalArgumentException ex) {
            throw new BadRequestException(ErrorCode.FIELD_ENUM_INVALID_VALUE, apiPricingType);
        }
    }

}
