package com.digitinary.dgate.model.apispec.policy;

import com.digitinary.dgate.exception.BadRequestException;
import com.digitinary.dgate.exception.ErrorCode;
import com.fasterxml.jackson.annotation.JsonCreator;

/**
 * HttpExchange enum.
 *
 * @author Ra'ad Khatatbeh
 * @since 7/02/2024
 */
public enum HttpExchange {

    REQUEST, RESPONSE, SYSTEM_REQUEST, SYSTEM_RESPONSE;

    /**
     * from value.
     *
     * @param httpExchange         type
     * @return HttpExchange        Http Exchange
     * @throws BadRequestException BadRequestException
     */
    @JsonCreator
    public static HttpExchange fromValue(final String httpExchange) {

        if (httpExchange == null || httpExchange.length() == 0) {
            throw new BadRequestException(ErrorCode.FIELD_ENUM_IS_EMPTY, httpExchange);
        }
        try {
            return HttpExchange.valueOf(httpExchange);
        } catch (IllegalArgumentException ex) {
            throw new BadRequestException(ErrorCode.FIELD_ENUM_INVALID_VALUE, httpExchange);
        }
    }
}
