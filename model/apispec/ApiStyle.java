package com.digitinary.dgate.model.apispec;

import com.digitinary.dgate.exception.BadRequestException;
import com.digitinary.dgate.exception.ErrorCode;
import com.fasterxml.jackson.annotation.JsonCreator;

/**
 * Api service types.
 *
 * @author Raad Khatatbeh
 * @since 25/10/2023
 */
public enum ApiStyle {

    REST, SOAP, WEB_SOCKET, GRPC;

    /**
     * from value.
     *
     * @param type                 type
     * @return ApiType             Api Type
     * @throws BadRequestException BadRequestException
     */
    @JsonCreator
    public static ApiStyle fromValue(final String type) {

        if (type == null || type.length() == 0) {
            throw new BadRequestException(ErrorCode.FIELD_ENUM_IS_EMPTY,type);
        }
        try {
            return ApiStyle.valueOf(type);
        } catch (IllegalArgumentException ex) {
            throw new BadRequestException(ErrorCode.FIELD_ENUM_INVALID_VALUE,type);
        }
    }
}




