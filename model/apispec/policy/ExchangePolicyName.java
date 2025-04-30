package com.digitinary.dgate.model.apispec.policy;

import com.digitinary.dgate.exception.BadRequestException;
import com.digitinary.dgate.exception.ErrorCode;
import com.fasterxml.jackson.annotation.JsonCreator;

/**
 * Exchange policy name enum.
 *
 * @author Ra'ad Khatatbeh
 * @since 7/02/2024
 */
public enum ExchangePolicyName {

    //Request Policies
    REQUEST_RATE_LIMITER("RequestRateLimiter"),
    REQUEST_QUOTA("RequestQuota"),
    COPY_REQUEST_HEADER("CopyRequestHeaders"),
    ADD_REQUEST_HEADER("AddRequestHeadersIfNotPresent"),
    COPY_REQUEST_QUERY_PARAM("CopyRequestQueryParameters"),
    ADD_REQUEST_QUERY_PARAM("AddRequestQueryParameters"),
    JWS_VERIFICATION("JwsVerification"),
    MONETIZATION("Monetization"),
    REQUEST_BODY_MODIFIER("RequestBodyModifier"),
    JSON_TO_JSON_REQUEST_TRANSFORMER("JsonToJsonRequestTransformer"),
    JWS_REQUEST_HEADER_VERIFIER("JsonWebSignature"),
    BACKEND_SERVICE_AUTH("BackendServiceAuth"),

    //Response Policies
    RESPONSE_BODY_CACHE("ResponseBodyCache"),
    MOCK_RESPONSE("MockResponse"),
    JSON_TO_JSON_RESPONSE_TRANSFORMER("JsonToJsonResponseTransformer"),
    RESPONSE_BODY_MODIFIER("ResponseBodyModifier"),
    FLATTEN_JSON_RESPONSE("FlattenJsonResponse"),
    JWS_RESPONSE_HEADER_GENERATOR("JwsResponseHeaderGenerator");

    private final String value;

    ExchangePolicyName(final String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }

    /**
     * from value.
     *
     * @param policyName          type
     * @return ExchangePolicyName ExchangePolicyName
     * @throws BadRequestException BadRequestException
     */
    @JsonCreator
    public static ExchangePolicyName fromValue(final String policyName) {

        if (policyName == null || policyName.isEmpty()) {
            throw new BadRequestException(ErrorCode.FIELD_ENUM_IS_EMPTY, policyName);
        }

        try {
            return ExchangePolicyName.valueOf(policyName);
        } catch (IllegalArgumentException ex) {
            throw new BadRequestException(ErrorCode.FIELD_ENUM_INVALID_VALUE, policyName);
        }
    }
}
