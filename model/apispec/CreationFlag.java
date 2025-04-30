package com.digitinary.dgate.model.apispec;

import com.digitinary.dgate.exception.BadRequestException;
import com.digitinary.dgate.exception.ErrorCode;
import com.fasterxml.jackson.annotation.JsonCreator;

/**
 * Api creation flag.
 *
 * @author Ra'ad Khatatbeh
 * @since 31/03/2024
 */
public enum CreationFlag {

    ADDED, IMPORTED;

    /**
     * Converts a string representation of a creation flag into a {@link CreationFlag} enum value.
     *
     * @param flag The string representation of the creation flag.
     * @return The corresponding {@link CreationFlag} enum value.
     * @throws BadRequestException If the provided flag is null, empty, or does not match any valid enum value.
     */
    @JsonCreator
    public static CreationFlag fromValue(final String flag) throws BadRequestException {
        // Check if the flag is null or empty
        if (flag == null || flag.length() == 0) {
            throw new BadRequestException(ErrorCode.FIELD_ENUM_IS_EMPTY, flag);
        }

        try {
            // Attempt to convert the string to a CreationFlag enum value
            return CreationFlag.valueOf(flag);
        } catch (IllegalArgumentException ex) {
            // If the conversion fails (invalid enum value), throw a BadRequestException
            throw new BadRequestException(ErrorCode.FIELD_ENUM_INVALID_VALUE, flag);
        }
    }

}
