package com.digitinary.dgate.model.apispec;

import com.digitinary.dgate.exception.BadRequestException;
import com.digitinary.dgate.exception.ErrorCode;
import com.fasterxml.jackson.annotation.JsonCreator;

/**
 * Api spec status.
 *
 * @author Salah Abu Msameh
 * @since 09/06/2023
 */
public enum ApiStatus {

    DRAFT,
    PUBLISHED,
    UNPUBLISHED,
    DELETED;

    /**
     * from value.
     *
     * @param status               type
     * @return ApiStatus           Api Status
     * @throws BadRequestException BadRequestException
     */
    @JsonCreator
    public static ApiStatus fromValue(final String status) {

        if (status == null || status.length() == 0) {
            throw new BadRequestException(ErrorCode.FIELD_ENUM_IS_EMPTY,status);
        }
        try {
            return ApiStatus.valueOf(status);
        } catch (IllegalArgumentException ex) {
            throw new BadRequestException(ErrorCode.FIELD_ENUM_INVALID_VALUE,status);
        }
    }
}
